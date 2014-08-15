<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:mods="http://www.loc.gov/mods/v3" exclude-result-prefixes="mods"
    xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:srw_dc="info:srw/schema/1/dc-schema"
    xmlns:oai_dc="oai_dc" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:odl="http://odl.ox.ac.uk/odl-mods-extensions/1.0/" xmlns:mets="http://www.loc.gov/METS/"
    xmlns:default="http://www.loc.gov/METS/" xmlns:dcterms="dcterms"
    xmlns:lookup="http://vocab.ox.ac.uk/lookup" xmlns:ox="ox" extension-element-prefixes="lookup"
    xmlns:goobi="http://goobi.bodleian.ox.ac.uk">
    <!-- version 0.1 of mods_to_dc_multi.xsl created by Yvonne Aburrow, 12-02-2013 -->
    <xsl:output method="xml" indent="yes" doctype-public="http://www.w3.org/2001/XMLSchema-instance"
        name="xml"/>
    <!--<xsl:variable name="outputDir" select="test"/>-->
    <xsl:param name="outputDir" required="yes"/>

    <xsl:template match="/">
        <xsl:choose>
            <!--if there is only one file, process its metadata without hasPart or isPartOf being inserted -->
            <xsl:when test="count(//mets:fileSec/mets:fileGrp)=1">
                <xsl:for-each select="//mods:mods">
                    <!-- get /mets:mets/mets:fileSec/mets:fileGrp/mets:file/@ID -->
                    <xsl:for-each select="/mets:mets/mets:fileSec/mets:fileGrp">
                        <xsl:for-each select="mets:file">
                            <xsl:variable name="numFileId" select="position()"/>
                            <xsl:variable name="actualFileId">
                                <xsl:choose>
                                    <xsl:when test="$numFileId &lt; 10">
                                        <xsl:text>-000</xsl:text>
                                        <xsl:value-of select="$numFileId"/>
                                    </xsl:when>
                                    <xsl:when
                                        test="($numFileId = 10) or (($numFileId &gt; 10) and ($numFileId &lt; 100))">
                                        <xsl:text>-00</xsl:text>
                                        <xsl:value-of select="$numFileId"/>
                                    </xsl:when>
                                    <xsl:when
                                        test="($numFileId = 100) or (($numFileId &gt; 100) and ($numFileId &lt; 1000))">
                                        <xsl:text>-0</xsl:text>
                                        <xsl:value-of select="$numFileId"/>
                                    </xsl:when>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:variable name="fileLabel"
                                select="concat(/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6],$actualFileId)"/>
                            <xsl:variable name="location" select="concat($outputDir, $fileLabel)"/>
                            <xsl:variable name="filename" select="concat($location,'.xml')"/>
                            <xsl:value-of select="$filename"/>
                            <xsl:variable name="master" select="false()"/>
                            <!-- Creating  -->
                            <xsl:result-document href="{$filename}" format="xml">
                                <oai_dc:dc xmlns:dcterms1="http://purl.org/dc/terms/" xmlns:ox="ox"
                                    xmlns:dcterms="dcterms"
                                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                                    xmlns:oai_dc="oai_dc"
                                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                    xsi:schemaLocation="oai_dc file:/Q:/itsd/Digital.Bodleian/schema/generated_dc.xsd">
                                    <xsl:call-template name="modsMods">
                                        <xsl:with-param name="count" select="1"/>
                                        <xsl:with-param name="master" select="$master"/>
                                        <xsl:with-param name="fileId" select="$fileLabel"/>
                                    </xsl:call-template>
                                </oai_dc:dc>
                            </xsl:result-document>
                        </xsl:for-each>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:when>
            <!--if there is more than one file, process metadata for each file -->
            <xsl:when test="count(//mets:fileSec/mets:fileGrp)>1">
                <xsl:for-each select="//mets:fileSec/mets:fileGrp">
                    <xsl:choose>
                        <!-- if it is the first iteration, create the parent document -->
                        <xsl:when test="position()=1">
                            <xsl:variable name="fileId"
                                select="number(substring(/mets:mets/mets:fileSec/mets:fileGrp/mets:file[1]/@ID,6,9))"/>
                            <xsl:variable name="actualFileId" select="$fileId+1"/>
                            <xsl:variable name="fileLabel"
                                select="concat(/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6]/@name,$actualFileId)"/>

                            <xsl:variable name="location" select="concat($outputDir,$fileLabel)"/>
                            <xsl:variable name="filename" select="concat($location,'-master.xml')"/>
                            <xsl:variable name="master" select="true()"/>
                            <xsl:value-of select="$filename"/>
                            <!-- Creating  -->
                            <xsl:result-document href="{$filename}" format="xml">
                                <oai_dc:dc xmlns:dcterms1="http://purl.org/dc/terms/" xmlns:ox="ox"
                                    xmlns:dcterms="dcterms"
                                    xmlns:dc="http://purl.org/dc/elements/1.1/"
                                    xmlns:oai_dc="oai_dc"
                                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                    xsi:schemaLocation="oai_dc file:/Q:/itsd/Digital.Bodleian/schema/generated_dc.xsd">
                                    <xsl:for-each select="//mods:mods">
                                        <xsl:call-template name="modsMods">
                                            <xsl:with-param name="master" select="$master"/>
                                            <xsl:with-param name="fileId" select="$fileLabel"/>
                                        </xsl:call-template>
                                    </xsl:for-each>
                                    <xsl:for-each select="//mets:fileSec">
                                        <xsl:for-each
                                            select="/mets:mets/mets:fileSec/mets:fileGrp[1]/mets:file/mets:FLocat">
                                            <xsl:variable name="getfileid"
                                                select="tokenize(@xlink:href, '/')"/>
                                            <xsl:variable name="childFileId"
                                                select="substring-before(getfileid[last()],'.')"/>
                                            <dcterms:hasPart>
                                                <xsl:value-of select="$childFileId"/>
                                            </dcterms:hasPart>
                                        </xsl:for-each>
                                    </xsl:for-each>
                                </oai_dc:dc>
                            </xsl:result-document>
                        </xsl:when>
                        <!-- create the child documents -->
                        <xsl:otherwise>
                            <xsl:for-each select="/mets:mets/mets:fileSec/mets:fileGrp[1]">
                                <xsl:variable name="count" select="position()"/>
                                <xsl:variable name="master" select="false()"/>
                                <xsl:for-each select="mets:file">
                                    <xsl:variable name="fileId" select="number(substring(@ID,6,9))"/>
                                    <xsl:variable name="actualFileId" select="$fileId+1"/>
                                    <xsl:variable name="childFileLabel"
                                        select="concat(/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6]/@name,$actualFileId)"/>

                                    <xsl:variable name="childLocation"
                                        select="concat($outputDir,$childFileLabel)"/>
                                    <xsl:variable name="childFilename"
                                        select="concat($childLocation,'.xml')"/>
                                    <xsl:value-of select="$childFilename"/>
                                    <!-- Creating  -->
                                    <xsl:result-document href="{$childFilename}" format="xml">
                                        <oai_dc:dc xmlns:dcterms1="http://purl.org/dc/terms/"
                                            xmlns:ox="ox" xmlns:dcterms="dcterms"
                                            xmlns:dc="http://purl.org/dc/elements/1.1/"
                                            xmlns:oai_dc="oai_dc"
                                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                                            xsi:schemaLocation="oai_dc file:/Q:/itsd/Digital.Bodleian/schema/generated_dc.xsd">
                                            <xsl:for-each select="//mods:mods">
                                                <xsl:call-template name="modsMods">
                                                  <xsl:with-param name="count" select="$count"/>
                                                  <xsl:with-param name="master" select="$master"/>
                                                </xsl:call-template>
                                            </xsl:for-each>
                                            <!--get parent doc title-->
                                            <xsl:for-each
                                                select="/mets:mets/mets:fileSec/mets:fileGrp[1]/mets:file">

                                                <xsl:variable name="masterFileId"
                                                  select="/mets:mets/mets:dmdSec[1]/mets:mdWrap[1]/mets:xmlData[1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods'][1]/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi'][1]/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata'][6]/@name"/>

                                                <dcterms:isPartOf>
                                                  <xsl:value-of
                                                  select="concat($masterFileId,'-master')"/>
                                                </dcterms:isPartOf>
                                            </xsl:for-each>
                                        </oai_dc:dc>
                                    </xsl:result-document>
                                </xsl:for-each>
                            </xsl:for-each>
                        </xsl:otherwise>
                    </xsl:choose>
                    <!-- end of nested xsl:choose -->
                </xsl:for-each>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    <!--  MODS TEMPLATES -->
    <xsl:template name="modsMods">
       <!-- <xsl:param name="master" select="()"/>
        <xsl:param name="count" select="()"/>
        <xsl:param name="fileId" select="()"/> -->
        <xsl:for-each select="//mods:extension">
            <xsl:call-template name="modsExt">
                <xsl:with-param name="count" select="$count"/>
                <xsl:with-param name="master" select="$master"/>
                <xsl:with-param name="fileId" select="$fileId"/>
            </xsl:call-template>
        </xsl:for-each>
        <xsl:for-each select="//mods:titleInfo[@type='alternative']">
            <xsl:apply-templates select="."/>
        </xsl:for-each>
        <!-- apply all the other templates except mods:titleInfo, which has already been applied-->
        <xsl:apply-templates select="*[not(self::mods:titleInfo[1])]"/>
    </xsl:template>



    <xsl:template match="mods:extension" name="modsExt">
       <!-- <xsl:param name="count" select="()"/>
        <xsl:param name="master" select="()"/>
        <xsl:param name="fileId" select="()"/>-->
        <xsl:choose>
            <xsl:when test="$master=true()">
                <xsl:for-each
                    select="/default:mets/default:fileSec[1]/default:fileGrp[1]/default:file[1]/default:FLocat">
                    <dcterms:identifier type="ox:uuid">
                        <xsl:value-of
                            select="concat($fileId,'-master')"
                        />
                    </dcterms:identifier>
                    <dcterms:source type="ox:mediaId">
                        <xsl:value-of select="@ID[1]"/>
                    </dcterms:source>
                </xsl:for-each>
                <ox:sort>0</ox:sort>
            </xsl:when>
            <xsl:otherwise>
                <xsl:for-each
                    select="/default:mets/default:fileSec[1]/default:fileGrp[$count]/default:file[1]/default:FLocat">
                    <dcterms:identifier type="ox:uuid">
                        <xsl:value-of select="$fileId"/>
                    </dcterms:identifier>
                    <dcterms:source type="ox:mediaId">
                        <xsl:value-of select="@xlink:href"/>
                    </dcterms:source>
                </xsl:for-each>
                <ox:sort>
                    <xsl:value-of select="$count"/>
                </ox:sort>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:call-template name="goobi"/>
        <dcterms:type type="ox:risType">GEN</dcterms:type>
    </xsl:template>

    <!-- GOOBI-SPECIFIC TEMPLATES -->

    <xsl:template name="goobi">
        <xsl:for-each
            select="/mets:mets/mets:dmdSec/mets:mdWrap/mets:xmlData/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='mods']/*[namespace-uri()='http://www.loc.gov/mods/v3' and local-name()='extension']/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='goobi']/*[namespace-uri()='http://meta.goobi.org/v1.5.1/' and local-name()='metadata']">
            <xsl:if test="@name='TitleDocMain'">
                <dcterms:title>
                    <xsl:value-of select="."/>
                </dcterms:title>
            </xsl:if>

            <xsl:if test="@name='TitleDocMainShort'">
                <dcterms:alternative>
                    <xsl:value-of select="."/>
                </dcterms:alternative>
            </xsl:if>

            <xsl:if test="@name='Bearbeiter'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:contributor>
                            <xsl:value-of select="."/>
                            <xsl:text> (editor)</xsl:text>
                        </dcterms:contributor>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='Editor'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:contributor>
                            <xsl:value-of select="."/>
                            <xsl:text> (editor)</xsl:text>
                        </dcterms:contributor>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='Composer'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:creator>
                            <xsl:value-of select="."/>
                            <xsl:text> (composer)</xsl:text>
                        </dcterms:creator>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='Author'">
                <xsl:for-each select="goobi:displayName">
                    <xsl:if test="not(contains(.,','))">
                        <dcterms:author>
                            <xsl:value-of select="normalize-space(substring-after(.,','))"/>
                            <xsl:text> </xsl:text>
                            <xsl:value-of select="normalize-space(substring-before(.,','))"/>
                        </dcterms:author>
                    </xsl:if>
                </xsl:for-each>
            </xsl:if>

            <xsl:if test="@name='pathimagefiles'">
                <dcterms:source>
                    <xsl:value-of select="."/>
                </dcterms:source>
            </xsl:if>

            <xsl:if test="@name='shelfmarksource'">
                <dcterms:identifier type="ox:shelfmark">
                    <xsl:value-of select="."/>
                </dcterms:identifier>
            </xsl:if>

            <xsl:if test="@name='CatalogueIDSource'">
                <dcterms:identifier type="ox:shelfmark">
                    <xsl:value-of select="."/>
                </dcterms:identifier>
            </xsl:if>

            <xsl:if test="@name='CatalogueIDDigital'">
                <dcterms:identifier type="ox:uuid">
                    <xsl:value-of select="."/>
                </dcterms:identifier>
            </xsl:if>

            <xsl:if test="@name='PublicationYear'">
                <dcterms:date>
                    <xsl:value-of select="."/>
                </dcterms:date>
            </xsl:if>

            <xsl:if test="@name='singleDigCollection'">
                <dcterms:format>
                    <xsl:value-of select="."/>
                </dcterms:format>
            </xsl:if>
            
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
